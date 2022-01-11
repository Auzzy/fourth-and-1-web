<template>
    <p>Game ID: {{ this.gameId }}</p>
    <div>
        <div style="float: left;">
            <h3>Game State</h3>
            <p>Quarter: {{ this.quarterStr }}</p>
            <p>Play: {{ this.playnum }} / {{ this.playsPerQuarter }}</p>
            <p v-if="this.down">Down: {{ this.down }} and {{ this.firstDownYdline - this.ydline }}</p>
            <p>Ball at {{ this.ydlineStr }}</p>
            <p :style="this.youScoreStyle">{{ this.you.name }}: {{ this.you.score }}</p>
            <p :style="this.opponentScoreStyle">{{ this.opponent.name }}: {{ this.opponent.score }}</p>
        </div>
        <div v-if="this.lastOffenseJson !== null && this.lastDefenseJson !== null" style="float: left;">
            <play :offenseJson="this.lastOffenseJson" :defenseJson="this.lastDefenseJson" :size="8" />
        </div>
        <div v-if="this.lastEvents">
            <p v-for="event in this.lastEvents" :key="event">{{ event }}</p>
        </div>
        <div style="clear: both">&nbsp;</div>
    </div>
    <div v-if="this.phase === 'coin-flip-result'">
        <div>
            {{ this.receiving.name }} has won the toss and will receive the opening kick off.
        </div>
    </div>
    <div v-if="this.phase === 'halftime'">
        <div>
            Halftime! {{ this.kicking.name }} won the opening toss, so they'll kick off to start the second half.
        </div>
    </div>
    <div v-if="this.phase === 'kickoff' || this.phase === 'coin-flip-result' || this.phase === 'halftime'">
        <div v-if="this.youIsKicking">
            Choose which type of kick you want.
            {{ JSON.stringify(this.actions) }}
            <button type="button" v-for="action in this.actions" :key="action['name']" @click="performAction(action['name'])">{{ action["display"] }}</button>
        </div>
    </div>
    <div v-if="this.phase === 'play-selection'">
        <div v-if="this.youIsOffense">
            <span style="float: left;">Other actions: </span><button type="button" style="float: left;" v-for="action in this.actions" :key="action['name']" @click="performAction(action['name'])">{{ action["display"] }}</button>
            <div style="clear: both">&nbsp;</div>
        </div>
        <div v-for="card in this.cards" :key="card.id" style="display: inline-block; padding: 1px;" :class="{selected: this.selectedCard === card.id}">
            <div>
                <play :[cardDisplayProperty]="card" :size="4" @click="this.selectCard(card.id)" />
            </div>
            <select v-if="this.selectedCard === card.id" name="offset" style="align: center" @change="this.changeOffset">
                <option></option>
                <option value="-2">Left</option>
                <option value="-1">Center-Left</option>
                <option value="0">Center</option>
                <option value="1">Center-Right</option>
                <option value="2">Right</option>
            </select>
        </div>
    </div>
</template>

<script>
    import Play from './Play.vue'
    import { post, get } from '@/utils'
    import { socketConnect } from '@/utils'

    export default {
        name: "PlayGame",
        components: {
            Play
        },
        props: ["gameId", "youJson", "opponentJson", "gameJson"],
        data() {
            return {
                you: null,
                opponent: null,
                phase: "coin-flip-result",
                actions: [],
                offense: null,
                defense: null,
                kicking: null,
                receiving: null,
                playsPerQuarter: 0,
                ydline: 0,
                down: 1,
                firstDownYdline: 0,
                playnum: 0,
                quarter: 1,
                offenseCards: [],
                defenseCards: [],
                selectedCard: "",
                selectedOffset: null,
                lastOffenseJson: null,
                lastDefenseJson: null,
                lastEvents: []
            }
        },
        computed: {
            youIsOffense() {
                return this.offense && this.you.name === this.offense.name;
            },
            youIsKicking() {
                return this.kicking && this.you.name === this.kicking.name;
            },
            youScoreStyle() {
                return {fontWeight: (this.youIsOffense || this.youIsKicking) ? "bold" : "normal"};
            },
            opponentScoreStyle() {
                return {fontWeight: !(this.youIsOffense || this.youIsKicking) ? "bold" : "normal"};
            },
            ydlineStr() {
                if (this.ydline === 50) {
                    return "midfield";
                } else {
                    return this.ydline < 50 ? `own ${this.ydline}` : `opponent's ${100 - this.ydline}`;
                }
            },
            cardDisplayProperty() {
                return this.youIsOffense ? "offenseJson" : "defenseJson";
            },
            cards() {
                return this.youIsOffense ? this.offenseCards : this.defenseCards;
            },
            quarterStr() {
                if (this.quarter === 5) {
                    return "OT";
                } else if (this.quarter >= 6) {
                    return `OT${this.quarter - 4}`;
                } else {
                    return this.quarter.toString();
                }
            },
            actionNames() {
                return this.actions.map(action => action["name"]);
            }
        },
        methods: {
            loadGameState(game) {
                console.log(JSON.stringify(game));

                this.phase = game.phase;
                this.actions = game.actions;

                this.kicking = game.kicking;
                this.receiving = game.receiving;
                this.offense = game.offense;
                this.defense = game.defense;
                this.playsPerQuarter = game.playsPerQuarter;
                this.ydline = game.ydline;
                this.down = game.down;
                this.firstDownYdline = game.firstDownYdline;
                this.playnum = game.playnum;
                this.quarter = game.quarter;
            },
            selectCard(cardId) {
                if (this.selectedCard === cardId) {
                    this.selectedCard = "";
                    this.selectedOffset = null;
                    this.submitCardSelection();
                } else {
                    this.selectedCard = cardId;
                }
            },
            changeOffset(changeEvent) {
                this.selectOffset(changeEvent.target.value);
            },
            selectOffset(offset) {
                this.selectedOffset = (this.selectedCard === "" || offset === "" || offset === undefined || offset === null) ? null : offset;
                this.submitCardSelection();
            },
            async submitCardSelection() {
                var endpointName = this.youIsOffense ? "offense" : "defense";
                await post(`http://localhost:5000/game/${this.gameId}/play/select-${endpointName}`, {cardId: this.selectedCard, offset: this.selectedOffset});
            },
            async performAction(actionName) {
                if (!this.actionNames.includes(actionName)) {
                    return;
                }

                await post(`http://localhost:5000/game/${this.gameId}/action`, {action: actionName});
            },

            listenForKickoffResult() {
                var socket = socketConnect(this.gameId);
                socket.on("kick-result", playInfo => {
                    this.selectedCard = "";
                    this.selectedOffset = null;
                    
                    this.lastOffenseJson = null;
                    this.lastDefenseJson = null;
                    this.lastEvents = playInfo["events"];
                    
                    this.loadGameState(playInfo["game"]);
                });
            },
            listenForPlayResult() {
                var socket = socketConnect(this.gameId);
                socket.on("play-result", playInfo => {
                    this.selectedCard = "";
                    this.selectedOffset = null;

                    this.lastOffenseJson = playInfo["offense"];
                    this.lastDefenseJson = playInfo["defense"];
                    this.lastEvents = playInfo["events"];
                    
                    this.loadGameState(playInfo["game"]);
                });
            }
        },
        created: async function() {
            this.you = JSON.parse(this.youJson);
            this.opponent = JSON.parse(this.opponentJson);
            this.loadGameState(JSON.parse(this.gameJson));

            this.listenForKickoffResult();
            this.listenForPlayResult();

            await Promise.all([
                get("http://localhost:5000/plays/offense", response => {this.offenseCards = response.cards;}),
                get("http://localhost:5000/plays/defense", response => {this.defenseCards = response.cards;})
            ]);
        }
    }
</script>

<style>
.selected {
    border: 2px solid black;
}
</style>
