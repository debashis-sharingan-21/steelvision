import Image from "next/image";
import { colorForClass } from "@/lib/classColors";
import { Detection } from "@/lib/types";

export function BoundingBoxOverlay({
  src,
  alt,
  width,
  height,
  detections,
}: {
  src: string;
  alt: string;
  width: number;
  height: number;
  detections: Detection[];
}) {
  return (
    <div className="relative w-full overflow-hidden rounded-md border border-border bg-black" style={{ aspectRatio: `${width} / ${height}` }}>
      <Image src={src} alt={alt} fill unoptimized className="object-contain" />
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="absolute inset-0 h-full w-full"
        preserveAspectRatio="xMidYMid meet"
      >
        {detections.map((d, i) => {
          const color = colorForClass(d.class_name);
          const boxWidth = d.bbox.x_max - d.bbox.x_min;
          const boxHeight = d.bbox.y_max - d.bbox.y_min;
          const label = `${d.class_name} ${(d.confidence * 100).toFixed(1)}%`;
          return (
            <g key={i}>
              <rect
                x={d.bbox.x_min}
                y={d.bbox.y_min}
                width={boxWidth}
                height={boxHeight}
                fill="none"
                stroke={color}
                strokeWidth={Math.max(width, height) * 0.008}
              />
              <text
                x={d.bbox.x_min}
                y={Math.max(d.bbox.y_min - height * 0.015, height * 0.03)}
                fill={color}
                fontSize={height * 0.045}
                fontFamily="var(--font-geist-mono)"
                style={{ paintOrder: "stroke", stroke: "#000", strokeWidth: height * 0.008 }}
              >
                {label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
