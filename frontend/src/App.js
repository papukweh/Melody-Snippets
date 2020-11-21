import { useState } from 'react'
import MicRecorder from 'mic-recorder-to-mp3'
import axios from 'axios'
import { Document, Page, pdfjs } from 'react-pdf'
import { saveAs } from 'file-saver'

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`

const recorder = new MicRecorder({
  bitRate: 128
})

export default function App () {
  const [isRecording, setRecording] = useState(false)
  const [audio, setAudio] = useState(null)
  const [score, setScore] = useState(null)

  const onRecordButtonClick = () => {
    setRecording(true)
    recorder.start().then(() => {
      console.log('Recording!!')
    })
      .catch((e) => {
        console.error(e)
      })
  }

  const onStopButtonClick = () => {
    setRecording(false)
    recorder.stop().getMp3().then(([buffer, blob]) => {
      console.log('Finished recording!')
      const form = new FormData()
      const headers = {
        contentType: 'multipart/form-data',
        responseType: 'blob'
      }
      const file = new File(buffer, 'audio.mp3', {
        type: blob.type,
        lastModified: Date.now()
      })
      setAudio(file)
      form.append('file', file)
      axios.post('http://localhost:5000/convert', form, headers)
        .then((res) => {
          console.log(res)
          const blob = new Blob([res.data], { type: 'application/pdf' })
          console.log(blob)
          setScore(URL.createObjectURL(blob))
        })
        .catch((err) => console.log(err))
    })
      .catch((e) => {
        alert('We could not retrieve your message')
        console.log(e)
      })
  }

  const onPlayButtonClick = () => {
    if (audio) {
      const player = new Audio(URL.createObjectURL(audio))
      player.play()
    }
  }

  const saveScore = () => {
    saveAs(score, 'score.pdf')
  }

  const [numPages, setNumPages] = useState(null)
  const [pageNumber, setPageNumber] = useState(1)

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages)
    setPageNumber(1)
  }

  return (
    <div>
      { isRecording
        ? (<button onClick={onStopButtonClick}>Stop Recording</button>)
        : (<button onClick={onRecordButtonClick}>Start Recording</button>)
      }
      <button onClick={onPlayButtonClick}>Play</button>
      { score
        ? (
            <div>
              <button onClick={saveScore}>Save PDF</button>
              <Document file={score} onLoadSuccess={onDocumentLoadSuccess}>
              <Page pageNumber={pageNumber} />
              </Document>
              <p>Page {pageNumber} of {numPages}</p>
            </div>
          )
        : null }
      </div>
  )
}
