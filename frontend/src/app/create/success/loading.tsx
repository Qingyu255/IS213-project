import { Spinner } from "@/components/ui/spinner"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

export default function SuccessLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-md w-full shadow-lg">
        <CardHeader className="pb-0">
          <div className="w-full bg-muted rounded-full h-2.5 mb-6">
            <div 
              className="bg-primary h-2.5 rounded-full transition-all duration-500 ease-in-out animate-pulse"
              style={{ width: "33%" }}
            />
          </div>
          <h2 className="text-2xl font-bold text-center">
            Processing Payment
          </h2>
        </CardHeader>
        <CardContent className="pt-4 flex flex-col items-center">
          <div className="my-8 animate-in fade-in zoom-in-50 duration-500">
            <Spinner size="lg" />
          </div>
          <p className="text-muted-foreground text-center animate-in fade-in slide-in-from-bottom-5 duration-500">
            Please wait while we verify your transaction...
          </p>
        </CardContent>
      </Card>
    </div>
  )
} 