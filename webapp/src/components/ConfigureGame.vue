<template>
    <form @submit.prevent="this.submit()">
        <input type="number" id="plays" min="10" max="30" step="5" autocomplete="off" v-model="form.playsperquarter" /> 
        <button>Submit</button>
    </form>
</template>

<script>
import router from '@/router'
import { post } from '@/utils'

export default {
    name: "ConfigureGame",
    data() {
        return {
            form: {
                playsperquarter: 10
            }
        }
    },
    methods: {
        async submit() {
            await post("http://localhost:5000/game/create", this.form, response => {
                router.push({name: "ConfigureTeam", params: {gameId: response.gameid}});
            });
        }
    }
}
</script>
