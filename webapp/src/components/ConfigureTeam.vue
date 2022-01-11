<template>
    <p>Game ID: {{ this.gameId }}</p>
    <form v-if="this.status === 'input'" @submit.prevent="this.submit()">
        <input type="text" id="name" autocomplete="off" v-model="form.name" /> 
        <button>Submit</button>
    </form>
    <p v-if="this.status === 'waiting'">Waiting for opponent...</p>
    <p v-if="this.status === 'opponent'">Opponent will be {{ this.opponent.name }}!</p>
</template>

<script>
import router from '@/router'
import { post } from '@/utils'
import { socketConnect } from '@/utils'

export default {
    name: "ConfigureTeam",
    props: ["gameId"],
    data() {
        return {
            status: "input",
            opponent: "",
            form: {
                name: ""
            }
        }
    },
    methods: {
        async submit() {
            this.status = "waiting",

            window.localStorage.setItem("fourthand1", JSON.stringify({gameId: this.gameId, team: this.form.name}));

            await post(`http://localhost:5000/game/${this.gameId}/team/create`, this.form);
        }
    },
    created() {
        var socket = socketConnect(this.gameId);
        socket.on("game-ready", gameJson => {
            socket.off("game-ready");

            var opponent = gameJson.teams.filter(team => team.name != this.form.name);
            if (opponent.length != 1) {
                console.error(`Unexpected number of opponents: ${opponent.length}`);
                return;
            }

            this.opponent = opponent[0];
            this.status = "opponent";
            var you = gameJson.teams.filter(team => team.name === this.form.name)[0];
                
            setTimeout(() => {
                router.push({name: "PlayGame", params: {gameId: this.gameId, youJson: JSON.stringify(you), opponentJson: JSON.stringify(this.opponent), gameJson: JSON.stringify(gameJson)}})
            }, 1000);
        });

    }
}
</script>

