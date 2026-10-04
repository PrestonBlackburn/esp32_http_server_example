// One EventSource per page, fanned out to any number of subscribers.
//
// The dashboard partials each register a callback instead of opening their own
// connection. The device caps total sockets (max_open_sockets defaults to 7,
// with 3 reserved for internal use), so one stream per component would eat
// the whole budget with three or four widgets.

const App = (() => {
  const frames = new Set();
  const statuses = new Set();
  let es = null;

  const notify = (set, payload) => set.forEach((fn) => fn(payload));

  function connect() {
    if (es) return;    // opening or open; never open a second socket

    es = new EventSource('/events');

    // The server sends one unnamed frame per tick, so onmessage is enough.
    es.onmessage = (event) => {
      let frame;
      try {
        frame = JSON.parse(event.data);
      } catch (err) {
        return;    // one truncated frame should not kill every widget
      }
      notify(frames, frame);
    };

    // EventSource reconnects on its own, so there is nothing to do but reflect
    // the state. Note the mock simulates outages in wifi_up; it does not drop
    // the socket, so this only fires on a genuine disconnect.
    es.onopen = () => notify(statuses, 'open');
    es.onerror = () => notify(statuses, 'down');
  }

  return {
    onFrame(fn) {
      frames.add(fn);
      connect();
      return () => frames.delete(fn);
    },

    onStatus(fn) {
      statuses.add(fn);
      fn(es && es.readyState === EventSource.OPEN ? 'open' : 'connecting');
      connect();
      return () => statuses.delete(fn);
    },
  };
})();