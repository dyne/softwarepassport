import { useEffect, useState } from "react";

interface VProps {
  transactionId: string;
  label: string;
  verificationUrl: string;
  verificationParam: string;
}

const VerificationButton = ({ transactionId, label, verificationUrl, verificationParam }: VProps) => {
  const [data, setData] = useState({});
  const options = {
    method: "POST",
    body: JSON.stringify({
      data: {
        [verificationParam]: transactionId
      }
    }),
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
  };

  useEffect(() => {
    fetch(verificationUrl, options).then(r => r.json().then(r => { setData(r) }));
  }, [])

  return <>
    {transactionId &&
      <>
        <label htmlFor={transactionId} className="btn btn-xs modal-button">{label}</label>

        <input type="checkbox" id={transactionId} className="modal-toggle" />
        <div className="modal">
          <div className="relative text-left modal-box min-w-fit">
            <label htmlFor={transactionId} className="absolute btn btn-sm btn-circle right-2 top-2">✕</label>
            <h3 className="text-lg font-bold">Congratulations this is notarized on {label}!</h3>
            <pre className="py-4">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </div>
      </>}
  </>
}

export default VerificationButton
