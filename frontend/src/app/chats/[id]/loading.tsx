import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";

export default function ChatLoading() {
  return (
    <Card className="w-full flex flex-col h-full min-h-[80vh]">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-6 w-48 rounded"></div>
        </div>
        <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-4 w-64 rounded mt-2"></div>
      </CardHeader>
      <CardContent className="border-t border-gray-200 flex-1 p-6">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <div className="mt-2 text-gray-600">Loading chat...</div>
        </div>
      </CardContent>
    </Card>
  );
}
