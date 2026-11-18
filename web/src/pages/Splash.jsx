import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getToken } from "../api.js";
import { ART } from "../assets/art/index.js";
import { FallingPetals } from "../components/Art.jsx";

// Screen 1: brand splash. Moves on by itself after a moment, or on tap.
export default function Splash() {
  const navigate = useNavigate();
  const next = () => navigate(getToken() ? "/home" : "/welcome", { replace: true });

  useEffect(() => {
    const t = setTimeout(next, 3800);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="splash" onClick={next} role="button" aria-label="Continue">
      <FallingPetals count={9} />
      <div className="corner-art" style={{ top: -20, left: -30, width: 170, opacity: 0.75 }}>
        <img src={ART.corner} alt="" />
      </div>
      <div className="corner-art tr" style={{ top: -20, right: -30, width: 150, opacity: 0.6, transform: "scaleX(-1)" }}>
        <img src={ART.corner} alt="" />
      </div>

      <header className="splash-head">
        <img className="lotus-img lotus-in" src={ART.lotus} alt="HerRhythm logo" />
        <div className="brand">HerRhythm</div>
        <div className="tag">Track · Understand · Thrive</div>
      </header>

      {/* the illustration fills the space left under the title and never overlaps it */}
      <div className="splash-art">
        <img className="woman-img woman-in breathe-img" src={ART.woman} alt="" />
      </div>

      <div className="foot">
        Your personal
        <br />
        menstrual &amp; wellness companion
      </div>
      <div className="bar"><i /></div>
    </div>
  );
}
