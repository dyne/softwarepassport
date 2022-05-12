import { useEffect, useState } from "react";

const FabricModal = ({ fabric_tag }) => {
  const [data, setData] = useState({});
  const options = {
    method: "POST",
    body: JSON.stringify({
      data: {
        myFabricTag: fabric_tag
      }
    }),
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
  };

  useEffect(() => {
    fetch("https://apiroom.net/api/zenbridge/fabric-read", options).then(r => r.json().then(r => { setData(r) }));
  }, [])

  return (fabric_tag &&
    <>
      <label htmlFor={fabric_tag} className="btn btn-xs modal-button">fabric</label>

      <input type="checkbox" id={fabric_tag} className="modal-toggle" />
      <div className="modal">
        <div className="relative modal-box">
          <label htmlFor={fabric_tag} className="absolute btn btn-sm btn-circle right-2 top-2">✕</label>
          <h3 className="text-lg font-bold">Congratulations this is notarized on Fabric!</h3>
          <pre className="py-4">{JSON.stringify(data, null, 2)}</pre>
        </div>
      </div>
    </>)
}

export default FabricModal
