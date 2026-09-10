export const SAMPLE_CLASSES = [
  { class: "crazing", label: "Crazing" },
  { class: "inclusion", label: "Inclusion" },
  { class: "patches", label: "Patches" },
  { class: "pitted_surface", label: "Pitted surface" },
  { class: "rolled-in_scale", label: "Rolled-in scale" },
  { class: "scratches", label: "Scratches" },
] as const;

export async function fetchSampleFile(cls: string): Promise<File> {
  const res = await fetch(`/samples/${cls}.jpg`);
  const blob = await res.blob();
  return new File([blob], `${cls}.jpg`, { type: "image/jpeg" });
}
