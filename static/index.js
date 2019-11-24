'use strict';

const $ = q => document.querySelector(q);
const $$ = q => document.querySelectorAll(q);

Element.prototype.$ = function(cls) {
  return this.getElementsByClassName(cls)[0];
};

let ws;

// function openWebsocket() {
//   ws = new WebSocket(`ws://${window.location.host}/socket`);

//   ws.onopen = onWebsocketInit;
//   ws.onmessage = onWebsocketMessage;
// }

// function onWebsocketInit() {
//   send('init');
// }

// function onWebsocketMessage(e) {
//   const { data, type } = JSON.parse(e.data);

//   if (type === 'msg') {
//     addMessage(data);
//   } else if (type === 'data') {
//     if (data.players) {
//       let money = { copper: 0, silver: 0, gold: 0, electrum: 0, platin: 0 };

//       $$('.player').forEach(p => p.remove());
//       const playerTemplate = $('#player-template').content;
//       for (const i in data.players) {
//         const p = data.players[i];

//         const newPlayer = playerTemplate.cloneNode(true);
//         const node = newPlayer.firstElementChild;
//         node.id = 'player-' + i;

//         for (const key in p) {
//           node.$(key).innerText = p[key];
//           if (key in money) money[key] += p[key];
//         }

//         $('.players').appendChild(newPlayer);
//       }

//       for (const key in money) {
//         $('.total').$(key).innerText = money[key];
//       }
//     }
//     if (data.map_images) {
//       $$('#map-bg option:not(.default)').forEach(el => el.remove());

//       for (let bg of data.map_images) {
//         const el = document.createElement('option');
//         el.value = '/img/maps/' + bg;
//         el.innerText = bg
//           .split('.')
//           .slice(0, -1)
//           .join(' ');
//         $('#map-bg').appendChild(el);
//       }
//     }
//     if (data.map) {
//       map.lines = data.map.lines;
//       map.bg_image.src = data.map.bg_image;
//       map.grid_size = data.map.grid_size;
//       map.grid_x = data.map.grid_x;
//       map.grid_y = data.map.grid_y;
//       map.units = data.map.units;
//       map.visible_areas = data.map.visible_areas;
//       $('#map-bg').value = data.map.bg_image;
//       $('#grid-size').value = map.grid_size;
//       $('#grid-x').value = map.grid_x;
//       $('#grid-y').value = map.grid_y;
//       requestAnimationFrame(renderMap);
//     }
//     if (data.maps) {
//       maps = data.maps;
//     }
//     if (data.initiative) {
//       $$('.initiative-bar .initiative-cell').forEach(el => el.remove());
//       const template = $('#initiative-cell-template');

//       for (const unit of data.initiative.units) {
//         const newEl = template.content.cloneNode(true);
//         newEl.firstElementChild.$('name').innerText = unit.name;
//         newEl.firstElementChild.$('initiative').innerText = unit.initiative;
//         $('.initiative-bar').appendChild(newEl);
//       }

//       const activeIndex = data.initiative.activeIndex + 1;
//       $(`.initiative-bar .initiative-cell:nth-child(${activeIndex})`).classList.add('active');
//     }
//     closeDialog();
//   } else if (type === 'initiative-index') {
//     $$('.initiative-bar .initiative-cell').forEach(el => el.classList.remove('active'));
//     $(`.initiative-bar .initiative-cell:nth-child(${data + 1})`).classList.add('active');
//   }
// }

// function send(type, data) {
//   if (ws.readyState !== WebSocket.OPEN) {
//     console.error('WebSocket geschlossen');
//     return;
//   }
//   if (data === undefined) {
//     ws.send(type);
//   } else {
//     const msg = '!' + JSON.stringify({ type, data });
//     console.log('Sending: ' + msg);
//     ws.send(msg);
//   }
// }

console.log("loaded");
