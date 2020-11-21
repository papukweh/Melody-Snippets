import { useState } from 'react'
import MicRecorder from 'mic-recorder-to-mp3'
import axios from 'axios'
import { v4 } from 'uuid'
import { Document, Page, pdfjs } from 'react-pdf'
import { saveAs } from 'file-saver'
import { Button } from '@material-ui/core'
import StopIcon from '@material-ui/icons/Stop'
import RecordIcon from '@material-ui/icons/Mic'
import PlayIcon from '@material-ui/icons/PlayArrow'
import PauseIcon from '@material-ui/icons/Pause'
import SaveIcon from '@material-ui/icons/Save'
import MidiIcon from '@material-ui/icons/MusicNote'

import './App.css'

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`

const recorder = new MicRecorder({
  bitRate: 320
})

export default function App () {
  const [isRecording, setRecording] = useState(false)
  const [isPlaying, setPlaying] = useState(false)
  const [isProcessing, setProcessing] = useState(false)
  const [audio, setAudio] = useState(null)
  const [midi, setMidi] = useState(null)
  const [score, setScore] = useState(null)

  const onStartRecordingButtonClick = () => {
    setRecording(true)
    recorder.start().then(() => {
      console.log('Recording!!')
    })
      .catch((e) => {
        console.error(e)
      })
  }

  const onStopRecordingButtonClick = () => {
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
      setAudio(new Audio(URL.createObjectURL(file), { onEnded: onStopButtonClick }))
      form.append('file', file)
      setProcessing(true)
      const filename = v4()
      axios.post(`http://localhost:5000/convert?filename=${filename}`, form, headers)
        .then((res) => {
          const blob = new Blob([res.data], { type: 'application/pdf' })
          setScore(URL.createObjectURL(blob))
          axios.get(`http://localhost:5000/get_midi/${filename}`, headers)
            .then((res) => {
              const blob = new Blob([res.data], { type: 'audio/midi' })
              setMidi(URL.createObjectURL(blob))
              setProcessing(false)
            })
        })
        .catch((err) => console.log(err))
    })
      .catch((e) => {
        alert('We could not retrieve your message')
        console.log(e)
      })
  }

  const onStopButtonClick = () => {
    if (audio && isPlaying) {
      setPlaying(false)
      audio.pause()
      audio.currentTime = 0
    }
  }

  const onPauseButtonClick = () => {
    if (audio && isPlaying) {
      setPlaying(false)
      audio.pause()
    }
  }

  const onPlayButtonClick = () => {
    if (audio) {
      setPlaying(true)
      audio.play()
    }
  }

  const saveScore = () => {
    saveAs(score, 'score.pdf')
  }

  const saveMidi = () => {
    saveAs(midi, 'score.mid')
  }

  const [numPages, setNumPages] = useState(null)
  const [pageNumber, setPageNumber] = useState(1)

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages)
    setPageNumber(1)
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Melody Snippets</h1>
      </header>
      <body className="App-body">
        { isRecording
          ? (<Button variant="contained" color="secondary" onClick={onStopRecordingButtonClick} startIcon={<StopIcon />}>Stop Recording</Button>)
          : (<Button variant="contained" color="primary" onClick={onStartRecordingButtonClick} startIcon={<RecordIcon />}>Start Recording</Button>)
        }
        <div>
          <Button variant="contained" color="default" onClick={onPlayButtonClick} startIcon={<PlayIcon />}></Button>
          <Button variant="contained" color="default" onClick={onPauseButtonClick} startIcon={<PauseIcon />}></Button>
          <Button variant="contained" color="default" onClick={onStopButtonClick} startIcon={<StopIcon />}></Button>
        </div>
        {
          isProcessing
            ? (<span>Processing...</span>)
            : null
        }
        { score
          ? (
              <div>
                <Button variant="contained" color="primary" onClick={saveScore} startIcon={<SaveIcon />}>Save PDF</Button>
                <Button variant="contained" color="primary" onClick={saveMidi} startIcon={<MidiIcon />}>Save MIDI</Button>
                <Document file={score} onLoadSuccess={onDocumentLoadSuccess}>
                <Page pageNumber={pageNumber} />
                </Document>
                <p>Page {pageNumber} of {numPages}</p>
              </div>
            )
          : null }
      </body>
    </div>
  )
}
