export type DBError = {
	detail?: unknown;
	reason?: 'db-error';
};




export type HTTPValidationError = {
	detail?: Array<ValidationError>;
};



export type InexistentItem = {
	key?: string | null;
	detail?: unknown | null;
	reason?: 'inexistent-item';
};




export type InvalidData = {
	detail?: unknown;
	reason?: 'invalid-data';
};




export type Left_DBError_NoneType_ = {
	value?: DBError;
	tag?: 'left';
};




export type Left_DBError_Sequence_str__ = {
	value?: DBError;
	tag?: 'left';
};




export type Left_DBError_bool_ = {
	value?: DBError;
	tag?: 'left';
};




export type Left_Union_DBError__InvalidData__InexistentItem__NoneType_ = {
	value?: DBError | InvalidData | InexistentItem;
	tag?: 'left';
};




export type Left_Union_DBError__InvalidData__InexistentItem___A_ = {
	value?: DBError | InvalidData | InexistentItem;
	tag?: 'left';
};




export type Left_Union_DBError__InvalidData__InexistentItem__tuple_str___A__ = {
	value?: DBError | InvalidData | InexistentItem;
	tag?: 'left';
};




export type Right_DBError_NoneType_ = {
	value?: null;
	tag?: 'right';
};




export type Right_DBError_Sequence_str__ = {
	value?: Array<string>;
	tag?: 'right';
};




export type Right_DBError_bool_ = {
	value?: boolean;
	tag?: 'right';
};




export type Right_Union_DBError__InvalidData__InexistentItem__NoneType_ = {
	value?: null;
	tag?: 'right';
};




export type Right_Union_DBError__InvalidData__InexistentItem___A_ = {
	value?: unknown;
	tag?: 'right';
};




export type Right_Union_DBError__InvalidData__InexistentItem__tuple_str___A__ = {
	value?: unknown[];
	tag?: 'right';
};




export type RootModel__A_ = {
};



export type ValidationError = {
	loc: Array<string | number>;
	msg: string;
	type: string;
};

