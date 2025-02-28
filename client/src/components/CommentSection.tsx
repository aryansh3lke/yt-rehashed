import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import IconButton from "@mui/material/IconButton";
import ThumbUpAltIcon from "@mui/icons-material/ThumbUpAlt";
import ThumbDownAltIcon from "@mui/icons-material/ThumbDownAlt";

import { Comment } from "../types/interfaces";

export default function CommentSection({
  comments,
  animationDelay,
}: {
  comments: Comment[];
  animationDelay: number;
}) {
  return (
    <section
      className="slide-up flex flex-col gap-8 md:w-1/2"
      style={{ animationDelay: `${animationDelay}s` }}
    >
      <p className="mt-5 text-center text-4xl md:text-5xl">Top Comments</p>
      <Card className="card-height" sx={{ overflowY: "auto", borderRadius: 2 }}>
        <CardContent>
          <ul className="my-2 flex flex-col gap-4 md:mx-5">
            {comments.map((comment) => (
              <li key={comment.cid} className="flex flex-row gap-4">
                <img
                  className="float-left h-[50px] w-[50px] rounded-full bg-repeat object-cover"
                  src={comment.photo}
                  alt={comment.author}
                ></img>
                <div className="flex flex-col gap-2">
                  <p className="flex flex-row flex-wrap items-center justify-start gap-2">
                    <strong>{comment.author}</strong>
                    <small>{comment.time}</small>
                  </p>
                  <p className="text-left">{comment.text.trim()}</p>
                  <div className="flex flex-row items-center justify-start gap-2">
                    <IconButton sx={{ p: 0 }}>
                      <ThumbUpAltIcon />
                    </IconButton>
                    <small className="">{comment.votes}</small>
                    <IconButton sx={{ p: 0 }}>
                      <ThumbDownAltIcon />
                    </IconButton>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </section>
  );
}
