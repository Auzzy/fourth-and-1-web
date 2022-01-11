<template>
    <play v-for="offenseCard in offenseCards" :key="offenseCard.id" :offenseJson="offenseCard" :size="4" />
    <play v-for="defenseCard in defenseCards" :key="defenseCard.id" :defenseJson="defenseCard" :size="4" />
    <hr />
    <play v-for="play in playResults" :key="play.offense.id + '-' + play.defense.id" :offenseJson="play.offense" :defenseJson="play.defense" :size="13" />
</template>

<script>
import Play from './Play.vue'
import { get } from '@/utils'

export default {
    name: 'DisplayAllPlays',
    data: function(){
        return {
            offenseCards: [],
            defenseCards: []
        }
    },
    computed: {
        playResults() {
            return this.offenseCards.flatMap(offCard => this.defenseCards.map(defCard => {return {offense: offCard, defense: defCard};}));
        }
    },
    components: {
        Play
    },
    created: async function() {
        await Promise.all([
			get("http://localhost:5000/plays/offense", response => {this.offenseCards = response.cards;}),
			get("http://localhost:5000/plays/defense", response => {this.defenseCards = response.cards;})
        ]);
    }
}
</script>
