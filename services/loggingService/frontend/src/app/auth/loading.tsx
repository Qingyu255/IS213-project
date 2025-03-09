import { Spinner } from '@/components/ui/spinner';
import React from 'react';

export default function loading() {
    return (
        <div className='h-[100vh]'>
            <div className='h-full flex items-center justify-center'>
                <Spinner size="lg" className='bg-black dark:bg-white'/>
            </div>
        </div>
    )
}
