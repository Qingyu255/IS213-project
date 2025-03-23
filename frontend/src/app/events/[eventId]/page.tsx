import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

const handleRefundClick = () => {
  router.push(`/events/${eventId}/refund`);
};

{isRegistered && (
  <Button
    variant="outline"
    onClick={handleRefundClick}
    className="w-full md:w-auto"
  >
    Request Refund
  </Button>
)} 