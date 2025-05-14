import { Node } from "./GDM-TS/src/Graph/node";
import { Edge } from "./GDM-TS/src/Graph/edge";

export class Link {
  constructor(
    public srcIndex: number,
    public tgtIndex: number,
    public link: string[],
  ) {}
}

export class CustomEdge extends Edge {
  constructor(
    src: string,
    tgt: string,
    probability: Array<[string, number]>,
    public links: Link[],
  ) {
    super(src, tgt, probability);
  }
}

export class CustomNode extends Node {
  public visitedCount: number;
  public sumPercentCompleted: number;
  public levels: string[][];
  public depth: number;

  private designerReward: number;
  private playerReward: number;

  constructor(
    name: string,
    reward: number,
    utility: number,
    isTerminal: boolean,
    neighbors: string[],
    levels: string[][],
    depth: number,
  ) {
    super(name, reward, utility, isTerminal, neighbors);

    this.designerReward = reward;
    this.playerReward = 0; // currently not using this, but may in the future
    this.levels = levels;
    this.depth = depth;

    this.visitedCount = 1;
    this.sumPercentCompleted = 1;
  }

  public updateReward(): void {
    this.reward = this.designerReward * this.visitedCount;
  }
}
