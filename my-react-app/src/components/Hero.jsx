import Button from './Button.jsx'
import logo from '../assets/logofullform.png'

export default function Hero() {
  return (
    <section id="top" className="hero reveal-section" data-shock-id="hero">
      <div className="hero__copy">
        <p className="eyebrow">Webcam form check · no gear, no gym required</p>
        <h1 className="hero__title">FULL FORM</h1>
        <p className="hero__sub">
          Open your webcam, run your set, and get told — rep by rep — exactly
          what your joints are doing wrong. No spotter, no mirror guesswork,
          no ego lifting.
        </p>
        <div className="hero__actions">
          <Button href="#start" variant="solid" size="lg">Upload file</Button>
          <Button href="#how" variant="outline" size="lg">See how it works</Button>
        </div>
        <p className="hero__note">Runs in the browser. Your video never leaves your device.</p>
      </div>
      <div className="hero__visual">
        <img src={logo} alt="FULL FORM logo" className="hero__image" />
      </div>
    </section>
  )
}
