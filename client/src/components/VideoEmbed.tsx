import { useEffect, useRef } from "react";

export default function VideoEmbed({
  videoId,
  seekTime,
}: {
  videoId: string;
  seekTime: number;
}) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (iframeRef.current && seekTime !== null) {
      iframeRef.current.contentWindow?.postMessage(
        JSON.stringify({
          event: "command",
          func: "seekTo",
          args: [seekTime, true],
        }),
        "*",
      );
    }
  }, [seekTime]);

  return (
    <iframe
      ref={iframeRef}
      className="h-full w-full"
      src={`https://www.youtube.com/embed/${videoId}?enablejsapi=1`}
      loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
      title="YouTube Video Player"
    />
  );
}
