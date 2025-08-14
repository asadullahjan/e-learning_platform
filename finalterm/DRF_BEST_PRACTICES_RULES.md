# Django REST Framework Best Practices Rules

## 🎯 **Core Principle: Separation of Concerns**

Each component should have **ONE** responsibility and **ONE** job only.

---

## 📝 **1. SERIALIZERS - Data Validation & Transformation ONLY**

### ✅ **What Serializers SHOULD Do:**

- Validate incoming data
- Transform data between Python objects and JSON
- Handle field-level validation
- Convert data types

### ❌ **What Serializers SHOULD NEVER Do:**

- Make database queries
- Import models
- Store state/data
- Handle business logic
- Create/update objects

### 🔧 **Examples:**

#### ❌ **WRONG - Business Logic in Serializer:**

```python
class ChatRoomSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        # ❌ WRONG: Database query in serializer
        existing_chat = ChatRoom.objects.filter(
            chat_type="direct",
            participants__user_id=attrs['participants'][0]
        ).first()

        # ❌ WRONG: Storing state on serializer
        if existing_chat:
            self.existing_chat = existing_chat

        return attrs
```

#### ✅ **CORRECT - Pure Validation Only:**

```python
class ChatRoomSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        chat_type = attrs.get("chat_type")
        participants = attrs.get("participants", [])

        # ✅ CORRECT: Only validation logic
        if chat_type == "direct" and len(participants) != 1:
            raise serializers.ValidationError(
                "Direct chats must have exactly 1 participant"
            )

        if chat_type == "course" and not attrs.get("course"):
            raise serializers.ValidationError(
                "Course is required for course-wide chat"
            )

        return attrs
```

---

## 🎭 **2. VIEWS - Request/Response Orchestration ONLY**

### ✅ **What Views SHOULD Do:**

- Handle HTTP requests/responses
- Call appropriate services
- Return serialized data
- Handle status codes
- Basic permission checks

### ❌ **What Views SHOULD NEVER Do:**

- Complex business logic
- Database queries (except basic filtering)
- Creating related objects
- Data manipulation
- Permission logic (should use permission classes)

### 🔧 **Examples:**

#### ❌ **WRONG - Business Logic in View:**

```python
class ChatRoomViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        # ❌ WRONG: Business logic in view
        chat_room = serializer.save(created_by=self.request.user)

        # ❌ WRONG: Creating related objects in view
        for user_id in participants:
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user_id=user_id,
                role="participant"
            )

        # ❌ WRONG: Complex logic in view
        if chat_room.chat_type == "direct":
            # Handle direct chat logic...
            pass
```

#### ✅ **CORRECT - Orchestration Only:**

```python
class ChatRoomViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ✅ CORRECT: Delegate to service
        chat_room = ChatService.create_chat_room(
            creator=request.user,
            chat_data=serializer.validated_data
        )

        response_serializer = ChatRoomListSerializer(chat_room)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
```

---

## 🏗️ **3. SERVICES - Business Logic Layer**

### ✅ **What Services SHOULD Do:**

- Handle all business logic
- Make database queries
- Create/update/delete objects
- Handle complex operations
- Business rules and workflows

### 🔧 **Examples:**

#### ✅ **CORRECT - Service Layer:**

```python
class ChatService:
    @staticmethod
    def create_chat_room(creator: User, chat_data: dict) -> ChatRoom:
        """Create chat room with all business logic"""

        # Handle existing direct chat check
        if chat_data['chat_type'] == 'direct':
            existing_chat = ChatService._find_existing_direct_chat(
                creator,
                chat_data['participants'][0]
            )
            if existing_chat:
                return existing_chat

        # Create chat room
        chat_room = ChatRoom.objects.create(
            name=chat_data['name'],
            chat_type=chat_data['chat_type'],
            created_by=creator,
            course=chat_data.get('course')
        )

        # Add participants based on chat type
        ChatService._add_participants_to_chat(chat_room, creator, chat_data['participants'])

        return chat_room

    @staticmethod
    def _find_existing_direct_chat(user1: User, user2: User) -> Optional[ChatRoom]:
        """Find existing direct chat between users"""
        return ChatRoom.objects.filter(
            chat_type="direct",
            participants__user_id=user1.id
        ).filter(
            participants__user_id=user2.id
        ).first()

    @staticmethod
    def _add_participants_to_chat(chat_room: ChatRoom, creator: User, participant_ids: List[int]):
        """Add participants with appropriate roles"""
        # Creator gets admin role for group/course chats
        role = "admin" if chat_room.chat_type != "direct" else "participant"

        ChatParticipant.objects.create(
            chat_room=chat_room,
            user=creator,
            role=role
        )

        # Add other participants
        for user_id in participant_ids:
            ChatParticipant.objects.create(
                chat_room=chat_room,
                user_id=user_id,
                role="participant"
            )
```

---

## 🔒 **4. PERMISSIONS - Centralized Access Control**

### ✅ **What Permissions SHOULD Do:**

- Handle all access control logic
- Check user permissions
- Validate object-level access
- Centralize security rules

### ❌ **What Permissions SHOULD NEVER Do:**

- Business logic
- Data manipulation
- Database queries (except for permission checks)

### 🔧 **Examples:**

#### ❌ **WRONG - Scattered Permission Logic:**

```python
class ChatRoomViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=["post"])
    def add_participants(self, request, pk=None):
        # ❌ WRONG: Permission logic scattered in views
        if not self._is_user_admin(chat, request.user):
            return Response(
                {"error": "Only admins can add participants"},
                status=status.HTTP_403_FORBIDDEN,
            )
```

#### ✅ **CORRECT - Centralized Permissions:**

```python
class ChatRoomPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == "create":
            return self._can_create_chat(request)
        return True

    def has_object_permission(self, request, view, obj):
        if view.action == "add_participants":
            return self._can_manage_participants(request.user, obj)
        if view.action in ["update", "destroy"]:
            return self._can_modify_chat(request.user, obj)
        return self._can_view_chat(request.user, obj)

    def _can_create_chat(self, request):
        chat_type = request.data.get("chat_type")
        if chat_type == "course":
            return request.user.role == "teacher"
        return True

    def _can_manage_participants(self, user, chat):
        try:
            participant = chat.participants.get(user=user)
            return participant.role == "admin"
        except ChatParticipant.DoesNotExist:
            return False
```

---

## 🗄️ **5. MODELS - Data Structure & Basic Methods**

### ✅ **What Models SHOULD Do:**

- Define data structure
- Basic model methods
- Model-level validation
- Relationships
- Meta options

### ❌ **What Models SHOULD NEVER Do:**

- Complex business logic
- API-specific logic
- Permission logic

### 🔧 **Examples:**

#### ✅ **CORRECT - Clean Model:**

```python
class ChatRoom(models.Model):
    CHAT_TYPE_CHOICES = [
        ("direct", "Direct"),
        ("group", "Group"),
        ("course", "Course"),
    ]

    name = models.CharField(max_length=255)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_rooms"
        constraints = [
            models.UniqueConstraint(
                fields=["course", "chat_type"],
                condition=models.Q(chat_type="course"),
                name="unique_course_chat_type",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_chat_type_display()})"

    # ✅ CORRECT: Basic model methods only
    def get_participant_count(self):
        return self.participants.count()

    def is_user_participant(self, user):
        return self.participants.filter(user=user).exists()
```

---

## 📋 **6. FILE ORGANIZATION RULES**

### ✅ **Proper Structure:**

```
elearning/
├── models.py              # Data models only
├── serializers/           # Data validation & transformation
│   └── chat_serializers.py
├── views/                 # Request/response handling
│   └── chat_views.py
├── services/              # Business logic
│   └── chat_service.py
├── permissions/           # Access control
│   └── chat_permissions.py
└── urls.py               # URL routing
```

### ❌ **Wrong Structure:**

```
elearning/
├── views/
│   └── chat_views.py     # ❌ Contains business logic
├── serializers/
│   └── chat_serializers.py  # ❌ Contains database queries
└── models.py             # ❌ Contains business logic
```

---

## 🚨 **7. COMMON MISTAKES TO AVOID**

### **Mistake 1: Database Queries in Serializers**

```python
# ❌ WRONG
def validate(self, attrs):
    existing = ChatRoom.objects.filter(name=attrs['name']).exists()
    if existing:
        raise serializers.ValidationError("Name already exists")

# ✅ CORRECT - Use unique=True in model or handle in service
```

### **Mistake 2: Business Logic in Views**

```python
# ❌ WRONG
def create(self, request):
    # Complex business logic here...
    if condition1:
        do_something()
    elif condition2:
        do_something_else()

# ✅ CORRECT - Delegate to service
def create(self, request):
    result = BusinessService.handle_create(request.data)
    return Response(result)
```

### **Mistake 3: Permission Logic Scattered**

```python
# ❌ WRONG - Permission checks everywhere
def update(self, request, pk=None):
    if not self._check_permission(request.user, self.get_object()):
        return Response({"error": "No permission"}, 403)

# ✅ CORRECT - Use permission classes
permission_classes = [ChatRoomPermission]
```

---

## 🎯 **8. QUICK CHECKLIST**

Before writing code, ask yourself:

- [ ] **Serializer**: Am I only validating/transforming data?
- [ ] **View**: Am I only handling HTTP requests/responses?
- [ ] **Service**: Is my business logic in a service layer?
- [ ] **Permission**: Are my access controls centralized?
- [ ] **Model**: Am I only defining data structure?
- [ ] **Separation**: Does each class have ONE responsibility?

---

## 💡 **9. REMEMBER THIS**

> **"If you're writing business logic in a serializer, you're doing it wrong!"**
>
> **"If you're making database queries in a view, you're doing it wrong!"**
>
> **"If you're checking permissions in multiple places, you're doing it wrong!"**

---

## 🔄 **10. REFACTORING STEPS**

1. **Identify mixed responsibilities** in your current code
2. **Extract business logic** into service classes
3. **Move permission logic** into permission classes
4. **Keep serializers pure** - validation only
5. **Keep views thin** - orchestration only
6. **Test each layer independently**

---

_Follow these rules and your code will be clean, maintainable, and follow Django REST Framework best practices!_ 🚀
