const StatusBar = ({ status }) => {
  const all_states = status.map(s => s.state);
  const steps = {
    "clone": { start: 1, end: 2 },
    "reuse": { start: 3, end: 4 },
    "notarize": { start: 5, end: 6 },
    "license scan": { start: 7, end: 8 },
  }

  const getState = (step: string) => {
    const { start, end } = steps[step];
    const started = all_states.includes(start);
    const finished = all_states.includes(end);
    let content = "🤌🏼"
    let className = "step "

    if (finished) {
      content = "✔️"
      className = "step step-success"
    } else if (started) {
      content = "⏳"
      className = "step"
    }
    return (<li className={className} key={step} data-content={content}>
      {step}
    </li>)
  }

  return (
    <ul className="steps">
      {Object.keys(steps).map((step) => {
        return getState(step);
      })}
    </ul>
  )

}

export default StatusBar;
