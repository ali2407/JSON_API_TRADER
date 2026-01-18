import Sidebar from "@/components/Sidebar";

export default function TradesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-[#0a0e1a]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="h-16 border-b border-gray-800 flex items-center px-8">
          <p className="text-gray-400">Welcome back</p>
        </div>
        {children}
      </main>
    </div>
  );
}
