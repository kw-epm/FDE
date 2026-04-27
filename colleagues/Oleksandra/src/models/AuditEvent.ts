import { AuditEventType } from '../types/enums';

export class AuditEvent {
  public id: string;
  public type: AuditEventType;
  public timestamp: Date;
  public entityId: string;
  public entityType: 'visit' | 'task';
  public details: Record<string, any>;

  constructor(
    type: AuditEventType,
    entityId: string,
    entityType: 'visit' | 'task',
    details: Record<string, any> = {}
  ) {
    this.id = `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.type = type;
    this.timestamp = new Date();
    this.entityId = entityId;
    this.entityType = entityType;
    this.details = details;
  }

  toJSON() {
    return {
      id: this.id,
      type: this.type,
      timestamp: this.timestamp.toISOString(),
      entityId: this.entityId,
      entityType: this.entityType,
      details: this.details
    };
  }
}
