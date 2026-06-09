import "./globals.css";

export const metadata = {
  title: "MediBot",
  description: "MediAssist internal knowledge assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
