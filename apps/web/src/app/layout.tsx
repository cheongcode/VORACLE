import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VORACLE | VALORANT Scouting Intelligence',
  description: 'Professional VALORANT opponent scouting and analysis system',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-valorant-dark min-h-screen`}>
        {/* Background Effects */}
        <div className="fixed inset-0 bg-valorant-gradient pointer-events-none" />
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-glow-cyan opacity-30 pointer-events-none blur-3xl" />
        <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-glow-red opacity-20 pointer-events-none blur-3xl" />
        
        {/* Main Content */}
        <div className="relative z-10">
          {children}
        </div>
      </body>
    </html>
  );
}
