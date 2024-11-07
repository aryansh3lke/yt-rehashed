export interface Comment {
    cid: string;
    photo: string;
    author: string;
    time: string;
    text: string;
    votes: number;
}

export type Resolution = "" | "144p" | "180p" | "240p" | "360p" | "480p" | "720p" | "1080p" | "1440p" | "2160p";