import { useState } from 'react'
import MicRecorder from 'mic-recorder-to-mp3'
import axios from 'axios'

const recorder = new MicRecorder({
  bitRate: 128
})

export default function App () {
  const [isRecording, setRecording] = useState(false)

  const onClick = () => {
    if (isRecording) {
      setRecording(false)
      recorder.stop().getMp3().then(([buffer, blob]) => {
        console.log('Finished recording!')
        const form = new FormData()
        const headers = {
          'Content-Type': 'multipart/form-data'
        }
        const file = new File(buffer, 'audio.mp3', {
          type: blob.type,
          lastModified: Date.now()
        })
        form.append('file', file)
        axios.post('http://localhost:5000/convert', form, headers)
          .then((res) => console.log(res))
          .catch((err) => console.log(err))
        const player = new Audio(URL.createObjectURL(file))
        player.play()
      })
      .catch((e) => {
        alert('We could not retrieve your message')
        console.log(e)
      })
    } else {
      setRecording(true)
      recorder.start().then(() => {
        console.log('Recording!!')
      })
      .catch((e) => {
        console.error(e)
      })
    }
  }

  return (
    <div>
      <button onClick={onClick}>Record</button>
    </div>
  )
}
