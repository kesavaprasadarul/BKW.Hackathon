'use client';

import { DraftingCompass } from 'lucide-react';
import Link from 'next/link';

export function Navigation() {
  return (
    <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
      <div className="max-w-7xl mx-auto px-6 md:px-8 lg:px-12">
        <div className="flex items-center justify-between h-[56px]">
          {/* Logo and Brand */}
          <Link href="/" className="flex items-center gap-2.5 hover:opacity-80 transition-opacity">
            <DraftingCompass className="w-6 h-6 text-primary-blue" />
            <span className="text-lg font-semibold text-text-primary">Atrium AI</span>
          </Link>

          {/* Future: Navigation items could go here */}
          <div className="flex items-center gap-4">
            {/* Placeholder for user profile/settings */}
          </div>
        </div>
      </div>
    </nav>
  );
}
