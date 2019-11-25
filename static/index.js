'use strict';

const $ = q => document.querySelector(q);
const $$ = q => document.querySelectorAll(q);

Element.prototype.$ = function(cls) {
  return this.getElementsByClassName(cls)[0];
};

Element.prototype.removeChildren = function() {
  while (this.firstChild) this.removeChild(this.firstChild);
};

function toInt(val) {
  const result = parseInt(val);
  if (isNaN(result)) return 0;
  return result;
}

let ws, myIndex;

function login(name) {
  if (window.location.protocol === 'https://')
    ws = new WebSocket(`wss://${window.location.host}/socket`);
  else ws = new WebSocket(`ws://${window.location.host}/socket`);

  ws.onopen = () => send('login', name);
  ws.onmessage = onWebsocketMessage;
  ws.onclose = () => window.location.reload();
}

function onWebsocketMessage(e) {
  /**
   *  {
   *    players: [
   *      {
   *        name: "Hans",
   *        points: 3,
   *        status: "ready", // "not-ready", "guesser"
   *      }
   *    ],
   *    you: {
   *      index: 0,
   *      word: "Tree",
   *    },
   *    waiting: false,
   *    word: null,
   *  }
   */
  const data = JSON.parse(e.data);
  let allReady = true;
  console.log(data);

  // Hide login screen
  $('#login').classList.add('hidden');
  $('#game').classList.remove('hidden');

  // Set player sidebar
  const playersEle = $('#players');
  playersEle.removeChildren();
  for (const player of data.players) {
    const playerEle = document.createElement('li');
    playersEle.appendChild(playerEle);
    playerEle.innerText = player.name;

    if (player.status === 'ready') playerEle.classList.add('player-ready');
    else if (player.status === 'guesser') playerEle.classList.add('player-guesser');
    else if (player.status === 'disconnected') playerEle.classList.add('player-disconnected');
    else allReady = false;

    const pointsEle = document.createElement('span');
    pointsEle.classList.add('player-points');
    pointsEle.innerText = player.points;
    playerEle.appendChild(pointsEle);
  }

  myIndex = data.you.index;
  const me = data.players[myIndex];
  const mainEle = $('#main');

  mainEle.className = '';

  if (data.waiting) {
    mainEle.classList.add('waiting');
  } else if (data.word === null) {
    if (me.status === 'guesser') {
      mainEle.classList.add('guesser');
      $('#btn-choose-word').disabled = !allReady;
    } else {
      mainEle.classList.add('liar');
      if (data.you.word) {
        $('#liar-my-word').innerText = 'Your word is: ' + data.you.word;
        mainEle.classList.add('liar-status');
        if (me.status === 'ready') {
          mainEle.classList.add('liar-ready');
        }
      }
    }
  } else {
    if (me.status === 'guesser') {
      mainEle.classList.add('guesser-word');
      $('#guesser-word').innerText = 'The word is: ' + data.word;
      const choicesEle = $('#guesser-players');
      choicesEle.removeChildren();
      for (const i in data.players) {
        const player = data.players[i];
        if (player.status !== 'guesser') {
          const choiceEle = document.createElement('button');
          choiceEle.type = 'button';
          choiceEle.innerText = player.name;
          choiceEle.addEventListener('click', () => send('guess', toInt(i)));
          choicesEle.appendChild(choiceEle);
        }
      }
    } else {
      mainEle.classList.add('liar-word');
      $('#liar-word').innerText = 'The word is: ' + data.word;
    }
  }
}

function send(type, data = null) {
  if (ws.readyState !== WebSocket.OPEN) {
    console.error('WebSocket geschlossen');
    return;
  }
  const msg = JSON.stringify({ type, data });
  console.log('Sending: ' + msg);
  ws.send(msg);
}

document.addEventListener('DOMContentLoaded', function() {
  $('#login-form').addEventListener(
    'submit',
    function(event) {
      event.preventDefault();
      const name = $('#login-name').value;
      if (name) {
        login(name);
      }
    },
    false
  );
  $('#btn-start-game').addEventListener('click', function() {
    send('start-game');
  });
  $('#btn-choose-word').addEventListener('click', function() {
    send('choose-word');
  });
  $('#btn-liar-ready').addEventListener('click', function() {
    send('ready', myIndex);
  });
  $('#btn-liar-not-ready').addEventListener('click', function() {
    send('not-ready', myIndex);
  });
  $('#form-set-word').addEventListener(
    'submit',
    function(event) {
      event.preventDefault();
      send('set-word', {
        index: myIndex,
        word: $('#my-word').value,
      });
    },
    false
  );
});
