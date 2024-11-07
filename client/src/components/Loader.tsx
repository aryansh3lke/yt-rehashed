export default function Loader({
  loaderTrigger,
  loaderType
}: {
  loaderTrigger: boolean,
  loaderType: string
}) {
  return (
    <div className='loader-div'>
        {loaderTrigger && (
            <div className={`loader ${loaderType}`}></div>
        )}
    </div>
  )
}
