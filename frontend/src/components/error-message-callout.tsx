import { AlertCircle } from "lucide-react";

import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert";

type ErrorMessageCalloutProps = {
    errorHeader?: string
    errorMessage: string
}

export function ErrorMessageCallout(props: ErrorMessageCalloutProps) {
    const {
        errorHeader = "Error",
        errorMessage,
    } = props;

    return (
        <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle className="font-bold">{errorHeader}</AlertTitle>
            <AlertDescription>
                {errorMessage}
            </AlertDescription>
        </Alert>
    );
}
