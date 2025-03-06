export interface Caption {
  text: string;
  start: number;
  duration: number;
}

export interface Comment {
  cid: string;
  text: string;
  time: string;
  author: string;
  channel: string;
  votes: string;
  photo: string;
  heart: boolean;
  reply: boolean;
}

export type Resolution =
  | ""
  | "144p"
  | "180p"
  | "240p"
  | "360p"
  | "480p"
  | "720p"
  | "1080p"
  | "1440p"
  | "2160p";

export interface CreatorInfo {
  id: string;
  handle: string;
  title: string;
  statistics: {
    subscriberCount: number;
    videoCount: number;
    viewCount: number;
  };
  avatar: string;
  channel: string;
  backgroundPoints: string[];
  background: string;
  credibilityPoints: string[];
  credibilityScore: number;
  contentQualityScore: number;
  engagementScore: number;
}
