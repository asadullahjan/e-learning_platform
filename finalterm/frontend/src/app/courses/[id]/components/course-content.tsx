import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Course } from "@/lib/types";
import Typography from "@/components/ui/Typography";
import { Button } from "@/components/ui/button";
import { Plus, FileText, Image, File, Video } from "lucide-react";

interface CourseContentProps {
  course: Course;
  isTeacher?: boolean;
}

const CourseContent = ({ course, isTeacher = false }: CourseContentProps) => {
  return (
    <div className="space-y-6">
      {/* Content Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Typography variant="h3" size="md">
              Course Content
            </Typography>
            {isTeacher && (
              <Button
                size="sm"
                className="transition-all duration-200 hover:bg-blue-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Content
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <Typography variant="p" color="muted" className="mb-4">
            Course materials and learning resources will be displayed here.
          </Typography>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
              <div>
                <Typography variant="p" className="font-medium">Text Lessons</Typography>
                <Typography variant="p" size="sm" color="muted">Written content and instructions</Typography>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <Image className="w-6 h-6 text-green-600" />
              <div>
                <Typography variant="p" className="font-medium">Images & Diagrams</Typography>
                <Typography variant="p" size="sm" color="muted">Visual learning materials</Typography>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <File className="w-6 h-6 text-purple-600" />
              <div>
                <Typography variant="p" className="font-medium">PDFs & Documents</Typography>
                <Typography variant="p" size="sm" color="muted">Reading materials and handouts</Typography>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <Video className="w-6 h-6 text-red-600" />
              <div>
                <Typography variant="p" className="font-medium">Videos & Audio</Typography>
                <Typography variant="p" size="sm" color="muted">Multimedia content</Typography>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Content Placeholder */}
      <Card>
        <CardHeader>
          <Typography variant="h3" size="md">
            Current Course Materials
          </Typography>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <Typography variant="p" color="muted" className="mb-2">
              No course materials uploaded yet
            </Typography>
            <Typography variant="p" size="sm" color="muted">
              Teachers can start adding content using the "Add Content" button above
            </Typography>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CourseContent;
