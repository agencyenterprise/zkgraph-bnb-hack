"use client";

type ButtonProps = {
  id: string;
  label: string;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
};

export default function Button({
  id,
  label,
  type = "submit",
  disabled,
  onClick,
  className,
}: ButtonProps) {
  return (
    <button
      id={id}
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${
        className || ""
      } rounded-md bg-primary-500 px-3.5 py-2.5 text-sm font-semibold text-tertiary-900 shadow-sm disabled:bg-secondary-400 hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500`}
    >
      {label}
    </button>
  );
}
