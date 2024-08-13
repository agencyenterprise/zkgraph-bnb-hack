const Loading = ({
  size,
  innerSize,
}: {
  size?: string;
  innerSize?: string;
}) => {
  return (
    <div
      className={`flex justify-center items-center
      ${!size && "h-screen w-screen"}`}
      style={size ? { height: size, width: size } : {}}
    >
      <div
        className={`animate-spin rounded-full border-t-2 border-b-2 border-primary-500 ${
          innerSize ? `h-${innerSize} w-${innerSize}` : "h-16 w-16"
        } `}
      ></div>
    </div>
  );
};

export default Loading;
