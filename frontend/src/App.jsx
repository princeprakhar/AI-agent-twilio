import React, { useState } from "react";
import MakeCall from "./components/MakeCall";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Agent for Call Automation with Twilio</h1>
        <MakeCall />
      </header>
    </div>
  );
}

// ye react js hai front mai

export default App;