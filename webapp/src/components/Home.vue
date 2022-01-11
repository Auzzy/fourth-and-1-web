<template>
    <router-link :to="{ name: 'ConfigureGame' }">
        <button>New Game</button>
    </router-link>
    <br />
    <input id="invitation-code" type="text" autocomplete="off" v-model="gameId" />
    <router-link :to="{ name: 'ConfigureTeam', params: {gameId: this.gameId }}">
        <button>Invitation Code</button>
    </router-link>
    <br />
    <button v-if="this.savedGameData" @click="this.loadGame">Load Game</button>
</template>

<script>
import router from '@/router'
import { get } from '@/utils'

export default {
    name: 'Home',
    data() {
        return {
            gameId: ''
        }
    },
    computed: {
        savedGameData() {
            return window.localStorage.getItem("fourthand1");
        }
    },
    methods: {
        async loadGame() {
            if (this.savedGameData === null) {
                return;
            }

            const gameInfo = JSON.parse(this.savedGameData);
            console.log(JSON.stringify(gameInfo));

            await get(`http://localhost:5000/game/${gameInfo.gameId}/load`, response => {
                const teams = response.game.teams
                const [youJson, opponentJson] = gameInfo.team === teams[0].name ? teams : [teams[1], teams[0]];
                router.push({
                    name: "PlayGame",
                    params: {
                        gameId: gameInfo.gameId,
                        youJson: JSON.stringify(youJson),
                        opponentJson: JSON.stringify(opponentJson),
                        gameJson: JSON.stringify(response.game)
                    }
                })
            })
        }
    }
}
</script>

