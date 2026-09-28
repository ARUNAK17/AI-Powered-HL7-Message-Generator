import "./globals.css";

export const metadata = {
  title: "AI-Powered HL7 Message Generator",
  description: "Generate and validate HL7 v2 ADT and ORU messages."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
