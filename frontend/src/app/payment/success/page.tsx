"use client"

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import Link from 'next/link';
import { CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getBearerToken } from '@/utils/auth';
import { getErrorStringFromResponse } from '@/utils/common';

function PaymentSuccessContent() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'creating_event' | 'event_created'>('loading');
  const [message, setMessage] = useState('');
  const [eventId, setEventId] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const payment_intent = searchParams.get('payment_intent');
  const eventCreation = searchParams.get('description')?.includes('Event Creation Fee');

  useEffect(() => {
    const verifyPayment = async () => {
      if (!payment_intent) {
        setStatus('error');
        setMessage('No payment information found.');
        return;
      }

      try {
        // Verify the payment was successful
        const response = await fetch(`${BACKEND_ROUTES.billingService}/api/payment/verify`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ payment_intent_id: payment_intent }),
        });

        const data = await response.json();

        if (data.verified) {
          setStatus('success');
          setMessage('Your payment has been confirmed!');
          
          // Check if this is event creation payment
          if (eventCreation) {
            // If so, create the event using stored event data
            await createEvent();
          }
        } else {
          setStatus('error');
          setMessage(data.error || 'Unable to verify payment.');
        }
      } catch (err) {
        setStatus('error');
        setMessage('An error occurred while verifying your payment.');
        console.error("Payment verification error:", err);
      }
    };

    verifyPayment();
  }, [payment_intent, eventCreation]);

  const createEvent = async () => {
    try {
      setStatus('creating_event');
      setMessage('Creating your event...');
      
      // Get stored event data from localStorage
      const storedEventData = localStorage.getItem('pending_event_data');
      
      if (!storedEventData) {
        throw new Error('Event data not found. Please try creating your event again.');
      }
      
      const eventData = JSON.parse(storedEventData);
      
      // Add payment information to the event metadata
      eventData.paymentInfo = {
        payment_intent_id: payment_intent,
        payment_date: new Date().toISOString()
      };
      
      // Send the event data to create event API
      const response = await fetch(`${BACKEND_ROUTES.createEventServiceUrl}/api/v1/create-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': await getBearerToken()
        },
        body: JSON.stringify(eventData)
      });
      
      if (!response.ok) {
        throw new Error(await getErrorStringFromResponse(response));
      }
      
      const createdEvent = await response.json();
      setEventId(createdEvent.id || eventData.id);
      
      // Clear the localStorage data
      localStorage.removeItem('pending_event_data');
      
      setStatus('event_created');
      setMessage('Your event has been created successfully!');
    } catch (err) {
      console.error('Error creating event:', err);
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Failed to create your event. Please try again.');
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6">
      <div className="bg-card rounded-lg shadow-md p-6">
        <div className="text-center mb-6">
          {status === 'loading' && <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary mb-4" />}
          {status === 'creating_event' && <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary mb-4" />}
          {(status === 'success' || status === 'event_created') && <CheckCircle2 className="h-12 w-12 mx-auto text-green-600 mb-4" />}
          {status === 'error' && <AlertCircle className="h-12 w-12 mx-auto text-red-600 mb-4" />}
          
          <h1 className="text-2xl font-bold mb-2">
            {status === 'loading' ? 'Verifying Payment...' :
             status === 'creating_event' ? 'Creating Your Event...' :
             status === 'event_created' ? 'Event Created!' :
             status === 'success' ? 'Payment Successful!' :
             'Payment Verification Failed'}
          </h1>
          
          <p className="text-muted-foreground mb-6">{message}</p>
          
          {status === 'event_created' && (
            <div className="space-y-4">
              <p>Your event has been successfully created and is now live!</p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button onClick={() => router.push(`/events/${eventId}`)}>
                  View Your Event
                </Button>
                <Button variant="outline" onClick={() => router.push('/my-events')}>
                  Go to My Events
                </Button>
              </div>
            </div>
          )}
          
          {status === 'success' && !eventCreation && (
            <Button asChild>
              <Link href="/">Return to Home</Link>
            </Button>
          )}
          
          {status === 'error' && (
            <div className="space-y-4">
              <Button variant="outline" onClick={() => router.back()}>
                Go Back
              </Button>
              <div className="text-sm text-muted-foreground mt-4">
                If you were charged but see this error, please contact support with your payment ID: {payment_intent}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={<div className="max-w-lg mx-auto p-6">
      <div className="bg-card rounded-lg shadow-md p-6 text-center">
        <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary mb-4" />
        <h1 className="text-2xl font-bold mb-2">Verifying payment...</h1>
      </div>
    </div>}>
      <PaymentSuccessContent />
    </Suspense>
  );
} 