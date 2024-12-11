import React, { useState } from "react";
import axios from "axios";

const MakeCall = () => {
  const [phoneNumber, setPhoneNumber] = useState(""); // State for phone number input
  const [responseMessage, setResponseMessage] = useState(""); // State for response messages

  // Handle input change for phone number
  const handleInputChange = (e) => {
    setPhoneNumber(e.target.value);
  };

  // Function to make the call
  const handleMakeCall = async () => {
    if (!phoneNumber) {
      setResponseMessage("Please enter a valid phone number.");
      return;
    }


    try {
      const backendUrl =
        "http://127.0.0.1:8000/api/make_call";

      // Send request to backend
      const response = await axios.get(backendUrl, {
        params: { to_number: phoneNumber },
      });


      console.log(response)

      // Display success message
      setResponseMessage(
        `Call initiated successfully! Call SID: ${response.data.call_sid}`
      );
    } catch (error) {
      // Display error message
      setResponseMessage(
        `Failed to initiate the call. Error: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  };

  return (
    <div style={{ margin: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2>Make a Call</h2>
      <label htmlFor="phone-number">
        Enter Phone Number:
        <input
          type="tel"
          id="phone-number"
          value={phoneNumber}
          onChange={handleInputChange}
          placeholder="+1234567890"
          style={{
            marginLeft: "10px",
            padding: "5px",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />
      </label>
      <button
        onClick={handleMakeCall}
        style={{
          marginLeft: "10px",
          padding: "5px 10px",
          borderRadius: "5px",
          border: "none",
          backgroundColor: "#4CAF50",
          color: "white",
          cursor: "pointer",
        }}
      >
        Call
      </button>
      {responseMessage && (
        <p
          style={{
            marginTop: "20px",
            color: responseMessage.includes("Failed") ? "red" : "green",
          }}
        >
          {responseMessage}
        </p>
      )}
    </div>
  );
};

export default MakeCall;