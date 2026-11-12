// "home_family" -> "Home family"
export function formatTopic(topic: string): string {
  const words = topic.replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}
