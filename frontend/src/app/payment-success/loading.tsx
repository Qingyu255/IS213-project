import { Spinner } from "@/components/ui/spinner"

export default function PaymentSuccessLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="max-w-md w-full p-6 bg-card rounded-lg shadow-lg text-center py-8">
        <Spinner className="mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-2">Processing Payment</h2>
        <p className="text-muted-foreground">
          Please wait while we complete your transaction...
        </p>
      </div>
    </div>
  )
} 