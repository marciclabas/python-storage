import type { CancelablePromise } from './core/CancelablePromise';
import { OpenAPI } from './core/OpenAPI';
import { request as __request } from './core/request';

import type { Left_DBError_bool_,Left_DBError_NoneType_,Left_DBError_Sequence_str__,Left_Union_DBError__InvalidData__InexistentItem___A_,Left_Union_DBError__InvalidData__InexistentItem__NoneType_,Left_Union_DBError__InvalidData__InexistentItem__tuple_str___A__,Right_DBError_bool_,Right_DBError_NoneType_,Right_DBError_Sequence_str__,Right_Union_DBError__InvalidData__InexistentItem___A_,Right_Union_DBError__InvalidData__InexistentItem__NoneType_,Right_Union_DBError__InvalidData__InexistentItem__tuple_str___A__,RootModel__A_ } from './models';

export type DefaultData = {
        InsertInsertPost: {
                    key: string
requestBody: RootModel__A_
                    
                };
ReadReadGet: {
                    key: string
                    
                };
HasHasGet: {
                    key: string
                    
                };
DeleteDeleteDelete: {
                    key: string
                    
                };
    }

export class DefaultService {

	/**
	 * Insert
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static insertInsertPost(data: DefaultData['InsertInsertPost']): CancelablePromise<Left_DBError_NoneType_ | Right_DBError_NoneType_> {
		const {
key,
requestBody,
} = data;
		return __request(OpenAPI, {
			method: 'POST',
			url: '/insert',
			query: {
				key
			},
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Read
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static readReadGet(data: DefaultData['ReadReadGet']): CancelablePromise<Left_Union_DBError__InvalidData__InexistentItem___A_ | Right_Union_DBError__InvalidData__InexistentItem___A_> {
		const {
key,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/read',
			query: {
				key
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Has
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static hasHasGet(data: DefaultData['HasHasGet']): CancelablePromise<Left_DBError_bool_ | Right_DBError_bool_> {
		const {
key,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/has',
			query: {
				key
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * Keys
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static keysKeysGet(): CancelablePromise<Left_DBError_Sequence_str__ | Right_DBError_Sequence_str__> {
				return __request(OpenAPI, {
			method: 'GET',
			url: '/keys',
		});
	}

	/**
	 * Values
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static valuesValuesGet(): CancelablePromise<Array<Left_Union_DBError__InvalidData__InexistentItem___A_ | Right_Union_DBError__InvalidData__InexistentItem___A_>> {
				return __request(OpenAPI, {
			method: 'GET',
			url: '/values',
		});
	}

	/**
	 * Items
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static itemsItemsGet(): CancelablePromise<Array<Left_Union_DBError__InvalidData__InexistentItem__tuple_str___A__ | Right_Union_DBError__InvalidData__InexistentItem__tuple_str___A__>> {
				return __request(OpenAPI, {
			method: 'GET',
			url: '/items',
		});
	}

	/**
	 * Delete
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static deleteDeleteDelete(data: DefaultData['DeleteDeleteDelete']): CancelablePromise<Left_Union_DBError__InvalidData__InexistentItem__NoneType_ | Right_Union_DBError__InvalidData__InexistentItem__NoneType_> {
		const {
key,
} = data;
		return __request(OpenAPI, {
			method: 'DELETE',
			url: '/delete',
			query: {
				key
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

}