<template>
    <div class="play-card" :width="width" :height="height">
        <canvas :id="this.canvasId" :width="width" :height="height" />
    </div>
</template>

<script>
let uid = 0;

export default {
    name: 'Play',
    props: ["size", "offenseJson", "defenseJson"],
    data() {
        return {
            fieldBgColor: "green",
            width: 6 * (10 + (this.size - 1) * 5),
            height: 8 * (10 + (this.size - 1) * 5)
        }
    },
    provide() {
        return {
            // These are just helpers, so it makes sense to preserve their context.
            ydToPx: (yd) => this.ydToPx(yd),
            ydToX: (yd) => this.ydToX(yd),
            ydToY: (yd) => this.ydToY(yd),
            ydCoordToX: (coord) => this.ydCoordToX(coord),
            ydCoordToY: (coord) => this.ydCoordToY(coord),
            canvasId: this.canvasId,
            pathWidth: () => this.pathWidth,
            canvasX: () => this.canvasX(),
            canvasY: () => this.canvasY()
        }
    },
    beforeCreate() {
        this.uid = uid.toString();
        uid += 1;
    },
    computed: {
        canvasId() {
            return `play-${this.uid}-canvas`;
        }
    },
    watch: {
        offenseJson() {
            this.draw();
        },
        defenseJson() {
            this.draw();
        }
    },
    methods: {
        canvasBoundingBox() {
            var canvas = document.getElementById(this.canvasId);
            return canvas.getBoundingClientRect();
        },
        canvasX() {
            return `${this.canvasBoundingBox().left}px`;
        },
        canvasY() {
            return `${this.canvasBoundingBox().top}px`;
        },
        ydToPx(yd) {
            return this.ydSepPx * yd;
        },

        ydToX(yd) {
            return this.fieldStartX + this.ydToPx(yd);
        },

        ydToY(yd) {
            return this.lineOfScrimmagePos + this.ydToPx(yd);
        },

        ydCoordToX(coord) {
            return this.ydToX(coord[0]);
        },

        ydCoordToY(coord) {
            return this.ydToY(coord[1]);
        },

        draw() {
            var canvas = document.getElementById(this.canvasId);
            this.ctx = canvas.getContext("2d");
            this.ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            if (this.offenseJson) {
                this.drawBallPath(this.offenseJson["path"]);
            }
            if (this.defenseJson) {
                this.drawDefense(this.defenseJson);
            }
            this.drawField();
        },

        // Draw a line marker every yard, and a thick line every 5 with a label.
        drawField() {
            this.ctx.globalCompositeOperation = "destination-over";
            this.ctx.fillStyle = "white";
            this.ctx.strokeStyle = "white";

            this.ctx.beginPath();
            this.ctx.lineWidth = 0.5;
            for (let yd = this.startYd; yd <= this.endYd; yd++) {
                var ydLinePos = this.lineOfScrimmagePos + yd * this.ydSepPx;

                if (yd % 5 == 0) {
                    this.ctx.stroke();
                    this.ctx.beginPath();

                    var ydLineWidth;
                    if (yd == 0) {
                        ydLineWidth = this.drawYdLine("LS", this.lineOfScrimmagePos);
                        this.ctx.fillRect(this.fieldStartX + ydLineWidth, this.lineOfScrimmagePos - 2, this.fieldWidth - 2 * ydLineWidth, 4);
                    } else {
                        this.ctx.lineWidth = 1.5;

                        ydLineWidth = this.drawYdLine(yd, ydLinePos);

                        this.ctx.moveTo(this.fieldStartX + ydLineWidth, ydLinePos);
                        this.ctx.lineTo(this.fieldEndX - ydLineWidth, ydLinePos);

                        this.ctx.stroke();
                    }

                    this.ctx.beginPath();
                    this.ctx.lineWidth = 0.5;
                } else {
                    this.ctx.moveTo(this.fieldStartX, ydLinePos);
                    this.ctx.lineTo(this.fieldEndX, ydLinePos);
                }
            }
            this.ctx.stroke();
        },

        drawYdLine(yd, yPos) {
            var ydLine = yd.toString();
            var ydLineWidth = this.ctx.measureText(ydLine).width + this.ydLineBuffer;

            this.ctx.textBaseline = "middle";
            this.ctx.font = "bold";
            this.ctx.fillText(ydLine, this.fieldStartX, yPos);
            this.ctx.fillText(ydLine, this.fieldEndX - ydLineWidth + this.ydLineBuffer, yPos);

            return ydLineWidth;
        },
        drawBallPath(pathJson) {
            this.ctx.globalCompositeOperation = "destination-over";
            this.ctx.beginPath();

            this.ctx.lineWidth = this.pathWidth;
            this.ctx.lineJoin = "miter";
            this.ctx.lineCap = "butt";
            this.ctx.strokeStyle = "black";

            var lastType = null;
            pathJson.forEach(node => {
                if (lastType === null || lastType !== node["type"]) {
                    this.ctx.stroke();
                    this.ctx.beginPath();

                    if (node["type"] === "pass" || node["type"] === "lateral") {
                        this.ctx.setLineDash([6, 5]);
                    } else if (node["type"] === "run") {
                        this.ctx.setLineDash([]);
                    } else if (node["type"] === "catch") {
                        this.ctx.setLineDash([]);
                        this.ctx.globalCompositeOperation = "source-over";
                        this.drawStar(this.ydCoordToX(node["start"]) + 1, this.ydCoordToY(node["start"]) - 1, 5, 4, 2, "red");
                        // To make sure the star isn't covered.
                        this.ctx.globalCompositeOperation = "destination-over";
                    }

                    this.ctx.moveTo(this.ydToX(node["start"][0]), this.ydToY(node["start"][1]));
                }

                this.ctx.lineTo(this.ydCoordToX(node["end"]), this.ydCoordToY(node["end"]));

                lastType = node["type"];
            });

            this.ctx.stroke();
        },
        // Adapted from: https://stackoverflow.com/a/25840319
        // Accessed 29 Dec 2021
        drawStar(cx, cy, spikes, outerRadius, innerRadius, color) {
            var rot = Math.PI / 2 * 3;
            var x = cx;
            var y = cy;
            var step = Math.PI / spikes;

            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.setLineDash([]);
            this.ctx.moveTo(cx, cy - outerRadius)
            for(let i = 0; i < spikes; i++) {
                x = cx + Math.cos(rot) * outerRadius;
                y = cy + Math.sin(rot) * outerRadius;
                this.ctx.lineTo(x, y);
                rot += step;

                x = cx + Math.cos(rot) * innerRadius;
                y = cy + Math.sin(rot) * innerRadius;
                this.ctx.lineTo(x, y);
                rot += step;
            }
            this.ctx.lineTo(cx, cy - outerRadius);
            this.ctx.closePath();
            this.ctx.strokeStyle = color;
            this.ctx.stroke();
            this.ctx.fillStyle = color;
            this.ctx.fill();
            this.ctx.restore();
        },
        drawDefense(cardJson) {
            this.ctx.globalCompositeOperation = "source-over";
            var defenderSize = 1;
            var radiusYd = defenderSize / 2;
            var defenderSizePx = this.ydToPx(defenderSize);

            this.ctx.fillStyle = "yellow";
            cardJson["players"]["tacklers"].forEach(coord => {
                this.ctx.beginPath();
                this.ctx.fillRect(this.ydToX(coord[0] - radiusYd), this.ydToY(coord[1] - radiusYd), defenderSizePx, defenderSizePx);
            });

            this.ctx.fillStyle = "blue";
            cardJson["players"]["fumblers"].forEach(coord => {
                this.ctx.beginPath();
                this.ctx.arc(this.ydCoordToX(coord), this.ydCoordToY(coord), this.ydToPx(radiusYd), 0, 2 * Math.PI);
                this.ctx.fill();
            });
        }
    },
    created() {
        var cardWidth = this.width;
        var originY = cardWidth / 14;

        this.fieldWidth = cardWidth * 0.90;
        var border = cardWidth - this.fieldWidth;

        this.startYd = -7;
        this.endYd = 29;
        this.ydSepPx = cardWidth / 30;
        this.pathWidth = this.ydSepPx / 2;
        this.ydLineBuffer = 5;
        this.fieldStartX = border / 2;
        this.fieldEndX = cardWidth - (border / 2);
        this.lineOfScrimmagePos = originY + Math.abs(this.startYd) * this.ydSepPx;
    },
    mounted() {
        this.draw();
    }
}
</script>

<style>
.play-card {
    border: 1px solid #000000;
    left: 0px;
    top: 0px;
    display: inline-block;
    margin: 5px;
    background-color: green;
}
</style>

