import { Comment } from '../types/interfaces';

export default function CommentSection({
    comments,
    animationDelay
}: {
    comments: Comment[],
    animationDelay: number
}) {
    return (
        <section className="main-box-outer slide-up" style={{ animationDelay: `${animationDelay}s`}}>
            <h2 className="section-title">Popular Comments</h2>
            <div className="main-box-inner comment-box">
            <ul className="comment-list">
                {comments.map((comment) => (
                <li key={comment.cid} className="comment-item">
                    <img className="comment-profile" src={comment.photo} alt={comment.author}></img>
                    <div className="comment-main">
                    <p className="comment-header">
                        <strong>{comment.author}</strong>
                        <small>{comment.time}</small></p>
                    <p className="comment-text">{comment.text.trim()}</p>
                    <div className="comment-likes">
                        <img src={process.env.PUBLIC_URL + '/thumbs-up.svg'} alt={"Like Button"}></img>
                        <small className="comment-like-count">{comment.votes}</small>
                    </div>
                    </div>
                </li>
                ))}
            </ul>
            </div>
        </section>
    )
}
