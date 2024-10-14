import React from 'react'

export default function Loader({ loaderTrigger, loaderType }) {
  return (
    <div className='loader-div'>
        {loaderTrigger && (
            <div className={`loader ${loaderType}`}></div>
        )}
    </div>
  )
}
