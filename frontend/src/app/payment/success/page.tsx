"use client"

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { BACKEND_ROUTES } from "@/constants/backend-routes";

export default function PaymentSuccessPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const searchParams = useSearchParams();
  const payment_intent = searchParams.get('payment_intent');
  const payment_intent_client_secret = searchParams.get('payment_intent_client_secret');

  useEffect(() => {
    const verifyPayment = async () => {
      if (!payment_intent) {
        setStatus('error');
        setMessage('No payment information found.');
        return;
      }

      try {
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
          setMessage('Your payment has been confirmed! You will receive a confirmation email shortly.');
        } else {
          setStatus('error');
          setMessage(data.error || 'Unable to verify payment.');
        }
      } catch (error) {
        setStatus('error');
        setMessage('An error occurred while verifying your payment.');
      }
    };

    verifyPayment();
  }, [payment_intent]);

  return (
    <div className="max-w-lg mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">
        {status === 'loading' ? 'Verifying Payment...' :
         status === 'success' ? 'Payment Successful!' :
         'Payment Verification Failed'}
      </h1>
      
      <div className={`p-4 rounded-lg ${
        status === 'loading' ? 'bg-blue-50 text-blue-700' :
        status === 'success' ? 'bg-green-50 text-green-700' :
        'bg-red-50 text-red-700'
      }`}>
        <p>{message}</p>
      </div>

      {status === 'success' && (
        <div className="mt-6">
          <a href="/" className="text-blue-600 hover:text-blue-800">
            Return to Home
          </a>
        </div>
      )}
    </div>
  );
} 