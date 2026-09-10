import { CheckCircle, WarningOctagon } from "@phosphor-icons/react/dist/ssr";

export function StatusBadge({ status }: { status: "PASS" | "DEFECT DETECTED" }) {
  const isPass = status === "PASS";
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-md border px-3 py-1.5 text-sm font-medium ${
        isPass
          ? "border-status-pass/30 bg-status-pass/10 text-status-pass"
          : "border-status-defect/30 bg-status-defect/10 text-status-defect"
      }`}
    >
      {isPass ? <CheckCircle size={18} weight="fill" /> : <WarningOctagon size={18} weight="fill" />}
      {status}
    </span>
  );
}
