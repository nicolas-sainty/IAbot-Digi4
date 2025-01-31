import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "@/app/globals.css";


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex flex-col">        <div id="header" className="bg-gray-200 p-4 ">
          <h1>Header</h1>
        </div>
        {children}
        <div id="footer" className="bg-gray-200 p-4 ">
          <h1>Footer</h1>
        </div>
    </div>
  );
}
