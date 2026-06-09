type LoaderProps = {
  label?: string;
  size?: "sm" | "md";
  inline?: boolean;
};

export function Loader({ label, size = "md", inline = false }: LoaderProps) {
  return (
    <div className={`loader-wrap${inline ? " loader-inline" : ""}`}>
      <span className={`loader-spinner loader-${size}`} aria-hidden="true" />
      {label && <span className="loader-label">{label}</span>}
    </div>
  );
}
