import { useEffect, useState } from "react";

const SawroomModal = ({ sawroom_tag }) => {
  const [data, setData] = useState({});
  const options = {
    method: "POST",
    body: JSON.stringify({
      data: {
        mySawroomTag: sawroom_tag
      }
    }),
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
  };

  useEffect(() => {
    fetch("https://apiroom.net/api/zenbridge/sawroom-read", options).then(r => r.json().then(r => { setData(r) }));
  }, [])

  return (sawroom_tag &&
    <>
      <label htmlFor={sawroom_tag} className="btn btn-xs modal-button">sawroom</label>

      <input type="checkbox" id={sawroom_tag} className="modal-toggle" />
      <div className="modal">
        <div className="relative modal-box">
          <label htmlFor={sawroom_tag} className="absolute btn btn-sm btn-circle right-2 top-2">✕</label>
          <h3 className="text-lg font-bold">Congratulations this is notarized on Sawroom!</h3>
          <pre className="py-4">{JSON.stringify(data, null, 2)}</pre>
        </div>
      </div>
    </>)
}

export default SawroomModal
