interface Holder {
  type: string;
  consolidated_copyright: string;
  consolidated_license_expression: string;
}
const CopyrightHolders = ({ holders }: { holders: Holder[] }) => {
  return (
    <div className="grid grid-cols-3 gap-8">
      {holders.map((holder: Holder) => {
        return (
          <div className="shadow-xl card w-96 bg-base-100">
            <div className="break-all card-body">
              <p className="whitespace-normal card-title">{holder.consolidated_copyright}</p>
              <p className="break-all whitespace-normal">{holder.consolidated_license_expression}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default CopyrightHolders
